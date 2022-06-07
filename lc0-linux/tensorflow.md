To build with tensorflow under linux you need to install Tensorflow_cc from
<https://github.com/FloopCZ/tensorflow_cc>. Either release v1.9.0, v1.12.0 or
v1.13.0. Tensorflow_cc requires a specific version of protobuf, which constrains
the build. Release v1.9.0 works out of the box, since the default protobuf
subproject (v3.5.1) is compatible and is used instead of a system installed
version. In contrast release v1.12.0 needs protobuf v3.6.0 and release v1.13.0
is built with protobuf 3.6.1 but also works with 3.6.0. For those versions
`-Dprotobuf-3-6-0=true` should be added to the build command line. Note that
this protobuf version has issues with static builds and crashes so is not
recommended for normal use. The crashes look very similar to:
* <https://github.com/protocolbuffers/protobuf/issues/5107>
* <https://github.com/protocolbuffers/protobuf/issues/5353>
