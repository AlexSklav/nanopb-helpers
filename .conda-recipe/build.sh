# Copy `nanopb-helpers` C source and headers to Arduino
cp lib/nanopb/src/*.h "${PREFIX}"/include/Arduino/nanopb/src

"${PYTHON}" version.py
rc=$?; if [[ $rc != 0  ]]; then exit $rc; fi
"${PYTHON}" setup.py install --single-version-externally-managed --record record.txt
rc=$?; if [[ $rc != 0  ]]; then exit $rc; fi
