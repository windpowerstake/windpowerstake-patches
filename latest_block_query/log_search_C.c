#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <string.h>

#define MAX_PATH_LENGTH 256


int main() {
    const char* dirPath = "./data/blockstore.db/";
    char lastLogFile[MAX_PATH_LENGTH] = {'\0'};

    DIR* dir = opendir(dirPath);
    if (dir == NULL) {
        fprintf(stderr, "Failed to open directory: %s\n", dirPath);
        return 1;
    }

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strstr(entry->d_name, ".log") != NULL) {
            char filePath[MAX_PATH_LENGTH];
            snprintf(filePath, MAX_PATH_LENGTH, "%s%s", dirPath, entry->d_name);

            if (strlen(lastLogFile) == 0 || strcmp(entry->d_name, lastLogFile) > 0) {
                strcpy(lastLogFile, entry->d_name);
            }
        }
    }

    closedir(dir);

    if (strlen(lastLogFile) == 0) {
        fprintf(stderr, "No log files found.\n");
        return 1;
    }

    char filePath[MAX_PATH_LENGTH];
    snprintf(filePath, MAX_PATH_LENGTH, "%s%s", dirPath, lastLogFile);

    FILE* file = fopen(filePath, "rb");
    if (file == NULL) {
        fprintf(stderr, "Failed to open file: %s\n", filePath);
        return 1;
    }

    fseek(file, 0, SEEK_END);
    long fileSize = ftell(file);
    rewind(file);

    char* buffer = (char*)malloc(fileSize);
    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate memory.\n");
        fclose(file);
        return 1;
    }

    fread(buffer, 1, fileSize, file);
    fclose(file);

    char outputString[MAX_PATH_LENGTH];
    outputString[0] = '\0';
    char prevChar = '\0';

    for (long i = fileSize - 1; i >= 0; --i) {
        char byte = buffer[i];
        if (byte == 'C' && prevChar == ':') {
            char output[MAX_PATH_LENGTH];
            output[0] = '\0';
            for (long j = i + 2; j < fileSize; ++j) {
                char byte2 = buffer[j];
                if ((unsigned char)byte2 > 127) {
                    strcat(output, "\n");
                    break;
                }
                char byteStr[2] = {byte2, '\0'};
                strcat(output, byteStr);
            }
            strcpy(outputString, output);
            break;
        }
        prevChar = byte;
    }

    free(buffer);

    printf("%s\n", outputString);

    return 0;
}

