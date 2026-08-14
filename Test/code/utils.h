// utils.h - common helper declarations
#ifndef LOCALMIND_UTILS_H
#define LOCALMIND_UTILS_H

#include <string>

namespace localmind {

// Compute SHA-256 hex digest of a file (stub for demo)
std::string file_hash(const std::string& path);

// Check whether a file extension is supported
bool is_supported_extension(const std::string& ext);

}  // namespace localmind

#endif  // LOCALMIND_UTILS_H
