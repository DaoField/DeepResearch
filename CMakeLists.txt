cmake_minimum_required(VERSION 3.15...3.26)

project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES NONE
)

find_package(Python REQUIRED COMPONENTS Interpreter)

# Install the Python package
install(DIRECTORY src/deepresearch DESTINATION .)
