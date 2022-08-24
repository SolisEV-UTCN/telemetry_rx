# Solis: Dashboard

## :clipboard:Prerequisites

Make sure the following are included inside your PATH:

- CMake 3.23.0
- Ninja 1.11.0
- Qt 6.3.0
- Visual Studio 2019 (optional)

## :dvd:Installation

1. Make sure you have all prerequisites
2. Create new project

   `git clone https://github.com/VorobiovM/solis_dashboard.git` 
3. Create make files

   For development with Visual Studio:
   
   `cmake --no-warn-unused-cli -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -Sc:<PATH_TO_PROJECT> -Bc:<PATH_TO_PROJECT>/build/target -G "Visual Studio 16 2019" -T host=x86 -A x64`
   
   For single executable:
   
   `cmake --no-warn-unused-cli -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -Sc:<PATH_TO_PROJECT> -Bc:<PATH_TO_PROJECT>/build/target -G Ninja`

4. Build project

   `cmake --build <PATH_TO_PROJECT>/build/target --config [Debug/Release/MinSizeRel/RelWithDebInfo] --target solis -j 10`
   
   **NOTE:** Use single config ex.: --config Debug
   
   **NOTE:** When in doubt use *Debug* config

## :star:Collaborators

- Blaj Matei
- Kasler Mada
- Muresan Alex
- Nemeth Raymond
- Vorobiov Misha
