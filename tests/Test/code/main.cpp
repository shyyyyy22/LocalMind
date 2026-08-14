// main.cpp - a small C++ demo program
#include <iostream>
#include <vector>
#include <string>

// A tiny in-memory file index for demo purposes
struct FileEntry {
    std::string path;
    std::string name;
    long long size;
};

int main() {
    std::vector<FileEntry> files;
    files.push_back({"D:/Test/docs/transformer_notes.md", "transformer_notes.md", 2048});
    files.push_back({"D:/Test/docs/ppo_notes.md", "ppo_notes.md", 1536});

    std::cout << "LocalMind C++ demo, indexed " << files.size() << " files." << std::endl;
    for (const auto& f : files) {
        std::cout << "  " << f.path << " (" << f.size << " bytes)" << std::endl;
    }
    return 0;
}
