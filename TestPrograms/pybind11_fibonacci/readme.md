Steps to run the example:

1. Execute Python example measuring time:

```
$ ptime python main.py

=== python main.py ===
24157817

Execution time: 6.417 s
```

2. Build C++ example and execute it measuring time

```
$ mkdir _build
$ cd _build
$ cmake .. -G "Visual Studio 16 2019"
...
$ cmake --build . --config Release
...
$ ptime Release\main.exe

=== Release\main.exe  ===
24157817

Execution time: 0.395 s
```

3. Install pybind11 library, build C++ binding code and execute the Python example using the generated module:

```
cd binding
mkdir _build
cd _build
conan install ..
...
$ cmake .. -G "Visual Studio 16 2019"
...
$ cmake --build . --config Release
...
$ cd ../..
...
$ ptime python main_cpp.py

=== python main_cpp.py ===
24157817

Execution time: 0.217 s
```
