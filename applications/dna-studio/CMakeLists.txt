cmake_minimum_required(VERSION 3.16)
project(DNAStudio VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets Svg SvgWidgets WebEngineWidgets Network)
qt_standard_project_setup()

# macOS app icon (compiled .icns lives in resources/)
set(MACOSX_BUNDLE_ICON_FILE DNAStudio.icns)
set(APP_ICON_MACOS ${CMAKE_CURRENT_SOURCE_DIR}/resources/DNAStudio.icns)
set_source_files_properties(${APP_ICON_MACOS} PROPERTIES
    MACOSX_PACKAGE_LOCATION "Resources"
)

qt_add_executable(dna-studio
    src/main.cpp
    src/MainWindow.cpp
    src/MainWindow.h
    src/Workspace.h
    src/LabConfig.h
    src/HttpServer.cpp
    src/HttpServer.h
    src/DnaStudioWorkspace.cpp
    src/DnaStudioWorkspace.h
    src/NotebookWorkspace.cpp
    src/NotebookWorkspace.h
    src/ProjectsWorkspace.cpp
    src/ProjectsWorkspace.h
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
    ${APP_ICON_MACOS}
)

target_link_libraries(dna-studio PRIVATE
    Qt6::Widgets
    Qt6::Svg
    Qt6::SvgWidgets
    Qt6::WebEngineWidgets
    Qt6::Network
)

set_target_properties(dna-studio PROPERTIES
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
    OUTPUT_NAME "DNA Studio"
    MACOSX_BUNDLE_BUNDLE_NAME "DNA Studio"
    MACOSX_BUNDLE_GUI_IDENTIFIER "com.michaelsedbon.dnastudio"
    MACOSX_BUNDLE_ICON_FILE DNAStudio.icns
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION}
)
