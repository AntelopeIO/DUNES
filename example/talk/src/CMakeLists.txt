project(talk)

set(EOSIO_WASM_OLD_BEHAVIOR "Off")
find_package(cdt)

add_contract( talk talk talk.cpp )
target_include_directories( talk PUBLIC ${CMAKE_SOURCE_DIR}/../include )
target_ricardian_directory( talk ${CMAKE_SOURCE_DIR}/../ricardian )