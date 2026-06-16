cmake_minimum_required(VERSION 3.16)
project(DNAStudio VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets Svg SvgWidgets)
qt_standard_project_setup()

qt_add_executable(dna-studio
    src/main.cpp
    src/MainWindow.cpp
    src/MainWindow.h
    src/CircularMapView.cpp
    src/CircularMapView.h
    src/SequenceIO.cpp
    src/SequenceIO.h
    src/SequenceDocument.h
    src/FeatureTypes.cpp
    src/FeatureTypes.h
    src/AnnotationDialog.cpp
    src/AnnotationDialog.h
    resources/resources.qrc
)

target_link_libraries(dna-studio PRIVATE
    Qt6::Widgets
    Qt6::Svg
    Qt6::SvgWidgets
)

set_target_properties(dna-studio PROPERTIES
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)
