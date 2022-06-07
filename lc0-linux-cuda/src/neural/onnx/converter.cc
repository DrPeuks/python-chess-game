/*
  This file is part of Leela Chess Zero.
  Copyright (C) 2021 The LCZero Authors

  Leela Chess is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Leela Chess is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with Leela Chess.  If not, see <http://www.gnu.org/licenses/>.

  Additional permission under GNU GPL version 3 section 7

  If you modify this Program, or any covered work, by linking or
  combining it with NVIDIA Corporation's libraries from the NVIDIA CUDA
  Toolkit and the NVIDIA CUDA Deep Neural Network library (or a
  modified version of those libraries), containing parts covered by the
  terms of the respective license agreement, the licensors of this
  Program grant you additional permission to convey the resulting work.
*/

#include "neural/onnx/converter.h"

#include <cstddef>
#include <initializer_list>
#include <memory>

#include "neural/loader.h"
#include "neural/network.h"
#include "neural/network_legacy.h"
#include "neural/onnx/adapters.h"
#include "neural/onnx/builder.h"
#include "neural/shared/policy_map.h"
#include "proto/net.pb.h"
#include "utils/exception.h"

namespace lczero {
namespace {

class Converter {
 public:
  Converter(const pblczero::Net& net,
            const WeightsToOnnxConverterOptions& options)
      : src_(net), options_(options) {}

  void Convert(pblczero::Net* dst);

 private:
  int NumFilters() const {
    return LayerAdapter(src_.weights().input().weights()).size() /
           kInputPlanes / 9;
  }
  size_t NumBlocks() const { return src_.weights().residual_size(); }
  void CopyGenericFields(pblczero::Net* dst);
  void GenerateOnnx(pblczero::OnnxModel* onnx);
  void FillValueInfo(pblczero::ValueInfoProto* vip, const std::string& name,
                     std::initializer_list<int> dims);

  std::string MakeConvBlock(OnnxBuilder* builder,
                            const LegacyWeights::ConvBlock&, int input_channels,
                            int output_channels, const std::string& input,
                            const std::string& name,
                            const LegacyWeights::SEunit* se_unit = nullptr,
                            const std::string& mixin = "", bool relu = true,
                            int filters = 3);

  std::string MakeResidualBlock(OnnxBuilder* builder,
                                const LegacyWeights::Residual&,
                                const std::string& input,
                                const std::string& name);

  std::string MakeSqueezeAndExcite(OnnxBuilder* builder,
                                   const LegacyWeights::SEunit& se_unit,
                                   const std::string& input,
                                   const std::string& name);

  void MakePolicyHead(pblczero::OnnxModel* onnx, OnnxBuilder* builder,
                      const std::string& input, const LegacyWeights& weights);

  void MakeValueHead(pblczero::OnnxModel* onnx, OnnxBuilder* builder,
                     const std::string& input, const LegacyWeights& weights);

  void MakeMovesLeftHead(pblczero::OnnxModel* onnx, OnnxBuilder* builder,
                         const std::string& input,
                         const LegacyWeights& weights);

  void AddStdInitializers(OnnxBuilder* builder);

  pblczero::TensorProto::DataType GetDataType() const;
  std::unique_ptr<OnnxConst> GetWeghtsConverter(
      const std::vector<float>&, std::initializer_list<int> dims,
      std::initializer_list<int> order = {});

  const pblczero::Net& src_;
  const WeightsToOnnxConverterOptions& options_;
};

pblczero::TensorProto::DataType Converter::GetDataType() const {
  switch (options_.data_type_) {
    case WeightsToOnnxConverterOptions::DataType::kFloat32:
      return pblczero::TensorProto::FLOAT;
    default:
      return pblczero::TensorProto::UNDEFINED;
  }
}

std::unique_ptr<OnnxConst> Converter::GetWeghtsConverter(
    const std::vector<float>& weights, std::initializer_list<int> dims,
    std::initializer_list<int> order) {
  switch (options_.data_type_) {
    case WeightsToOnnxConverterOptions::DataType::kFloat32:
      return std::make_unique<FloatOnnxWeightsAdapter>(weights, dims, order);
  }
  throw Exception("Data type " +
                  std::to_string(static_cast<int>(options_.data_type_)) +
                  " is not supported in weights converter");
}

std::string Converter::MakeSqueezeAndExcite(
    OnnxBuilder* builder, const LegacyWeights::SEunit& se_unit,
    const std::string& input, const std::string& name) {
  const int se_filters = se_unit.b1.size();

  auto flow = builder->GlobalAveragePool(name + "/pooled", input);
  flow = builder->Squeeze(name + "/squeeze", flow);
  flow = builder->MatMul(
      name + "/matmul1", flow,
      *GetWeghtsConverter(se_unit.w1, {NumFilters(), se_filters}, {1, 0}));
  flow = builder->Add(name + "/add1", flow,
                      *GetWeghtsConverter(se_unit.b1, {se_filters}));
  flow = builder->Relu(name + "/relu", flow);
  flow = builder->MatMul(
      name + "/matmul2", flow,
      *GetWeghtsConverter(se_unit.w2, {se_filters, 2 * NumFilters()}, {1, 0}));
  flow = builder->Add(name + "/add2", flow,
                      *GetWeghtsConverter(se_unit.b2, {2 * NumFilters()}));
  flow = builder->Reshape(name + "/reshape", flow, "/const/se_reshape");

  auto splits = builder->Split(name + "/split", flow, 1);

  flow = builder->Sigmoid(name + "/sigmoid", splits.first);
  flow = builder->Mul(name + "/matmul3", flow, input);
  return builder->Add(name + "/add3", flow, splits.second);
}

std::string Converter::MakeConvBlock(
    OnnxBuilder* builder, const LegacyWeights::ConvBlock& weights,
    int input_channels, int output_channels, const std::string& input,
    const std::string& name, const LegacyWeights::SEunit* seunit,
    const std::string& mixin, bool relu, int filters) {
  auto flow = builder->Conv(
      name, input,
      *GetWeghtsConverter(weights.weights,
                          {output_channels, input_channels, filters, filters}),
      *GetWeghtsConverter(weights.biases, {output_channels}),
      (filters - 1) / 2);

  if (seunit) flow = MakeSqueezeAndExcite(builder, *seunit, flow, name + "/se");
  if (!mixin.empty()) flow = builder->Add(name + "/mixin", flow, mixin);
  if (relu) flow = builder->Relu(name + "/relu", flow);
  return flow;
}

std::string Converter::MakeResidualBlock(OnnxBuilder* builder,
                                         const LegacyWeights::Residual& res,
                                         const std::string& input,
                                         const std::string& name) {
  auto block1 = MakeConvBlock(builder, res.conv1, NumFilters(), NumFilters(),
                              input, name + "/conv1");
  return MakeConvBlock(builder, res.conv2, NumFilters(), NumFilters(), block1,
                       name + "/conv2", res.has_se ? &res.se : nullptr, input);
}

void Converter::AddStdInitializers(OnnxBuilder* builder) {
  builder->AddInitializer("/const/se_reshape",
                          Int64OnnxConst({-1, NumFilters() * 2, 1, 1}, {4}));
}

namespace {
std::vector<int> MakePolicyMap() {
  std::vector<int> policy_map(1858);
  int idx = 0;
  for (const auto& mapping : kConvPolicyMap) {
    if (mapping > -1) policy_map[mapping] = idx;
    idx++;
  }
  return policy_map;
}
}  // namespace

void Converter::MakePolicyHead(pblczero::OnnxModel* onnx, OnnxBuilder* builder,
                               const std::string& input,
                               const LegacyWeights& weights) {
  if (!weights.policy1.weights.empty()) {
    // Conv policy head.
    auto flow = MakeConvBlock(builder, weights.policy1, NumFilters(),
                              NumFilters(), input, "/policy/conv1");
    flow = MakeConvBlock(builder, weights.policy, NumFilters(), 80, flow,
                         "/policy/conv2", nullptr, "", false);
    flow = builder->Reshape(
        "/policy/flatten", flow,
        builder->AddInitializer("/const/policy_shape",
                                Int64OnnxConst({-1, 80 * 8 * 8}, {2})));
    auto output = builder->Gather(
        options_.output_policy_head, flow,
        builder->AddInitializer("/const/mapping_table",
                                Int32OnnxConst(MakePolicyMap(), {1858})),
        {1});
    builder->AddOutput(output, {-1, 1858}, GetDataType());
    onnx->set_output_policy(output);
  } else {
    // Dense policy head.
    const int pol_channels = weights.policy.biases.size();
    auto flow =
        MakeConvBlock(builder, weights.policy, NumFilters(), pol_channels,
                      input, "/policy/conv", nullptr, "", true, 1);
    flow =
        builder->Reshape("/policy/reshape", flow,
                         builder->AddInitializer(
                             "/const/policy_shape",
                             Int64OnnxConst({-1, pol_channels * 8 * 8}, {2})));
    flow = builder->MatMul(
        "/policy/dense/matmul", flow,
        *GetWeghtsConverter(weights.ip_pol_w, {pol_channels * 8 * 8, 1858},
                            {1, 0}));
    auto output = builder->Add(options_.output_policy_head, flow,
                               *GetWeghtsConverter(weights.ip_pol_b, {1858}));
    builder->AddOutput(output, {-1, 1858}, GetDataType());
    onnx->set_output_policy(output);
  }
}

void Converter::MakeValueHead(pblczero::OnnxModel* onnx, OnnxBuilder* builder,
                              const std::string& input,
                              const LegacyWeights& weights) {
  auto flow = MakeConvBlock(builder, weights.value, NumFilters(), 32, input,
                            "/value/conv", nullptr, "", true, 1);
  flow = builder->Reshape(
      "/value/reshape", flow,
      builder->AddInitializer("/const/value_shape",
                              Int64OnnxConst({-1, 32 * 8 * 8}, {2})));
  flow = builder->MatMul(
      "/value/dense1/matmul", flow,
      *GetWeghtsConverter(weights.ip1_val_w, {32 * 8 * 8, 128}, {1, 0}));
  flow = builder->Add("/value/dense1/add", flow,
                      *GetWeghtsConverter(weights.ip1_val_b, {128}));
  flow = builder->Relu("/value/dense1/relu", flow);

  const bool wdl = src_.format().network_format().value() ==
                   pblczero::NetworkFormat::VALUE_WDL;
  if (wdl) {
    flow = builder->MatMul(
        "/value/dense2/matmul", flow,
        *GetWeghtsConverter(weights.ip2_val_w, {128, 3}, {1, 0}));
    flow = builder->Add("/value/dense2/add", flow,
                        *GetWeghtsConverter(weights.ip2_val_b, {3}));
    auto output = builder->Softmax(options_.output_wdl, flow);
    builder->AddOutput(output, {-1, 3}, GetDataType());
    onnx->set_output_wdl(output);
  } else {
    flow = builder->MatMul(
        "/value/dense2/matmul", flow,
        *GetWeghtsConverter(weights.ip2_val_w, {128, 1}, {1, 0}));
    flow = builder->Add("/value/dense2/add", flow,
                        *GetWeghtsConverter(weights.ip2_val_b, {1}));
    auto output = builder->Tanh(options_.output_value, flow);
    builder->AddOutput(output, {-1, 1}, GetDataType());
    onnx->set_output_value(output);
  }
}

void Converter::MakeMovesLeftHead(pblczero::OnnxModel* onnx,
                                  OnnxBuilder* builder,
                                  const std::string& input,
                                  const LegacyWeights& weights) {
  if (src_.format().network_format().moves_left() !=
      pblczero::NetworkFormat::MOVES_LEFT_V1) {
    return;
  }
  const int mlh_channels = weights.moves_left.biases.size();
  const int mlh_fc1_outputs = weights.ip1_mov_b.size();
  auto flow =
      MakeConvBlock(builder, weights.moves_left, NumFilters(), mlh_channels,
                    input, "/mlh/conv", nullptr, "", true, 1);
  flow = builder->Reshape(
      "/mlh/reshape", flow,
      builder->AddInitializer("/const/mlh_shape",
                              Int64OnnxConst({-1, mlh_channels * 8 * 8}, {2})));
  flow = builder->MatMul(
      "/mlh/dense1/matmul", flow,
      *GetWeghtsConverter(weights.ip1_mov_w,
                          {mlh_channels * 8 * 8, mlh_fc1_outputs}, {1, 0}));
  flow =
      builder->Add("/mlh/dense1/add", flow,
                   *GetWeghtsConverter(weights.ip1_mov_b, {mlh_fc1_outputs}));
  flow = builder->Relu("/mlh/dense1/relu", flow);
  flow = builder->MatMul(
      "/mlh/dense2/matmul", flow,
      *GetWeghtsConverter(weights.ip2_mov_w, {mlh_fc1_outputs, 1}, {1, 0}));
  flow = builder->Add("/mlh/dense2/add", flow,
                      *GetWeghtsConverter(weights.ip2_mov_b, {1}));
  auto output = builder->Relu(options_.output_mlh, flow);
  builder->AddOutput(output, {-1, 1}, GetDataType());
  onnx->set_output_mlh(output);
}

void Converter::GenerateOnnx(pblczero::OnnxModel* onnx) {
  LegacyWeights weights(src_.weights());
  OnnxBuilder builder;

  AddStdInitializers(&builder);

  onnx->set_input_planes(options_.input_planes_name);
  builder.AddInput(options_.input_planes_name, {-1, 112, 8, 8}, GetDataType());

  // Input convolution.
  auto flow = MakeConvBlock(&builder, weights.input, kInputPlanes, NumFilters(),
                            options_.input_planes_name, "/inputconv");

  // Residual tower.
  for (size_t i = 0; i < NumBlocks(); ++i) {
    flow = MakeResidualBlock(&builder, weights.residual[i], flow,
                             "/block" + std::to_string(i));
  }

  // Policy head.
  MakePolicyHead(onnx, &builder, flow, weights);
  // Value head.
  MakeValueHead(onnx, &builder, flow, weights);
  // Moves left head.
  MakeMovesLeftHead(onnx, &builder, flow, weights);

  onnx->set_model(builder.OutputAsString());
}

void Converter::CopyGenericFields(pblczero::Net* dst) {
  dst->set_license(src_.license());
  dst->set_magic(src_.magic());
  auto* min_version = dst->mutable_min_version();
  min_version->set_minor(28);
  auto* network_format = dst->mutable_format()->mutable_network_format();
  network_format->set_input(src_.format().network_format().input());
  network_format->set_output(src_.format().network_format().output());
  network_format->set_network(pblczero::NetworkFormat::NETWORK_ONNX);
  // We add convolution-to-classical layer to ONNX layers anyway, so from
  // outside they are all POLICY_CLASSICAL.
  network_format->set_policy(pblczero::NetworkFormat::POLICY_CLASSICAL);
  network_format->set_value(src_.format().network_format().value());
  network_format->set_moves_left(src_.format().network_format().moves_left());

  *dst->mutable_training_params() = src_.training_params();
}

void Converter::Convert(pblczero::Net* dst) {
  if (src_.has_onnx_model() && src_.format().network_format().network() ==
                                   pblczero::NetworkFormat::NETWORK_ONNX) {
    *dst = src_;
    return;
  }
  if (!src_.has_weights()) {
    throw Exception("The network doesn't have weights.");
  }
  if (src_.has_onnx_model()) {
    throw Exception("The network already has ONNX section.");
  }
  CopyGenericFields(dst);
  GenerateOnnx(dst->mutable_onnx_model());
}

}  // namespace

pblczero::Net ConvertWeightsToOnnx(
    const pblczero::Net& net, const WeightsToOnnxConverterOptions& options) {
  Converter converter(net, options);
  pblczero::Net dst;
  converter.Convert(&dst);
  return dst;
}

}  // namespace lczero
