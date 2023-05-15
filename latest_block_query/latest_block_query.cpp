#include <iostream>
#include <fstream>
#include <chrono>
#include <cstdlib>
#include <cstdio>
#include <cstring>

//I need to retrieve the last block in the most efficient way
//This means:
//Find the last .log file in blockstore.db
//reverse search for SC:Whatevertheblockis:NonASCIICharacter
//this reduces the block query time by more than 10 orders of magnitude

int main() {
    // Execute the command to find the last .log file
    FILE* pipe = popen("find ./data/blockstore.db/ -type f -name \"*.log\" -printf '%T@ %p\\n' | sort -nr | head -1 | cut -f2- -d\" \"", "r");
    if (!pipe) {
        std::cerr << "Error executing command." << std::endl;
        return 1;
    }

    const int bufferSize = 128;
    char buffer[bufferSize];

    if (fgets(buffer, bufferSize, pipe)) {
        // Remove the newline character from the result
        buffer[strcspn(buffer, "\n")] = '\0';

        // Process the last .log file
        const char* file_name = buffer;
        std::ifstream file(file_name, std::ios::binary | std::ios::ate);

        if (!file) {
            std::cerr << "Failed to open file: " << file_name << std::endl;
            pclose(pipe);
            return 1;
        }

        std::streampos fileSize = file.tellg();

        auto start = std::chrono::high_resolution_clock::now();  // Start time measurement

        char prevChar = '\0';

        for (std::streamoff i = static_cast<std::streamoff>(fileSize) - 1; i >= 0; --i) {
            file.seekg(i);
            char byte;
            file.read(&byte, 1);

            if (byte == 'C' && prevChar == ':') {
                std::cout << "I found it" << std::endl;

                // Now we're going to find out the first non-ASCII byte which marks when we stop writing the block
                for (std::streamoff j = i; j <= static_cast<std::streamoff>(fileSize) - 1; j++) {
                    file.seekg(j);
                    char byte2;
                    file.read(&byte2, 1);
                    std::cout << byte2 << std::endl;

                    if (static_cast<unsigned char>(byte2) > 127) {
                        std::cout << "Non-ASCII byte found: " << static_cast<int>(byte2) << std::endl;
                        break;
                    }
                }

                break;
            }

            prevChar = byte;
        }

        auto end = std::chrono::high_resolution_clock::now();  // End time measurement

        file.close();

        // Calculate the duration in microseconds
        auto durationUs = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();

        std::cout << "Time taken: " << durationUs << " microseconds" << std::endl;
    }

    pclose(pipe);

    return 0;
}
