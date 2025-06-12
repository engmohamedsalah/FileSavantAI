#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <dirent.h>
#include <pwd.h>
#include <grp.h>
#include <time.h>
#include <string.h>
#include <unistd.h>

// MCP Server for FileSavantAI - File Operations
void send_initialization();
void send_tools_list(int id);
void send_error(int id, const char* code, const char* message);
void handle_list_files(int id, const char* directory);
char* extract_string_value(const char* json, const char* key);
int extract_id(const char* json);

const char* get_file_type(mode_t mode) {
    if (S_ISDIR(mode)) return "directory";
    if (S_ISREG(mode)) return "file";
    if (S_ISLNK(mode)) return "symlink";
    if (S_ISCHR(mode)) return "char_device";
    if (S_ISBLK(mode)) return "block_device";
    if (S_ISFIFO(mode)) return "fifo";
    if (S_ISSOCK(mode)) return "socket";
    return "unknown";
}

void send_initialization() {
    printf("{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}\n");
    fflush(stdout);
}

void send_tools_list(int id) {
    printf("{\"jsonrpc\":\"2.0\",\"id\":%d,\"result\":["
           "{\"name\":\"list_files\","
           "\"description\":\"List all files in a directory\","
           "\"inputSchema\":{\"type\":\"object\",\"properties\":{\"directory\":{\"type\":\"string\",\"description\":\"Directory path\"}},\"required\":[\"directory\"]}}"
           "]}\n", id);
    fflush(stdout);
}

void send_error(int id, const char* code, const char* message) {
    printf("{\"jsonrpc\":\"2.0\",\"id\":%d,\"error\":{\"code\":\"%s\",\"message\":\"%s\"}}\n", 
           id, code, message);
    fflush(stdout);
}

void print_file_json_compact(const char *directory, const char *filename, struct stat *st, int first) {
    struct passwd *pwd = getpwuid(st->st_uid);
    struct group *grp = getgrgid(st->st_gid);
    const char *file_type = get_file_type(st->st_mode);
    
    char fullpath[2048];
    if (strcmp(directory, ".") == 0) {
        snprintf(fullpath, sizeof(fullpath), "%s", filename);
    } else {
        snprintf(fullpath, sizeof(fullpath), "%s/%s", directory, filename);
    }
    
    if (!first) printf(",");
    
    printf("{\"name\":\"%s\",\"path\":\"%s\",\"size\":%lld,\"owner\":\"%s\",\"group\":\"%s\","
           "\"uid\":%d,\"gid\":%d,\"permissions\":\"%03o\",\"permissions_readable\":\"",
           filename, fullpath, (long long)st->st_size, 
           pwd ? pwd->pw_name : "unknown", grp ? grp->gr_name : "unknown",
           st->st_uid, st->st_gid, st->st_mode & 0777);
    
    // Print permissions
    printf("%c", S_ISDIR(st->st_mode) ? 'd' : '-');
    printf("%c", (st->st_mode & S_IRUSR) ? 'r' : '-');
    printf("%c", (st->st_mode & S_IWUSR) ? 'w' : '-');
    printf("%c", (st->st_mode & S_IXUSR) ? 'x' : '-');
    printf("%c", (st->st_mode & S_IRGRP) ? 'r' : '-');
    printf("%c", (st->st_mode & S_IWGRP) ? 'w' : '-');
    printf("%c", (st->st_mode & S_IXGRP) ? 'x' : '-');
    printf("%c", (st->st_mode & S_IROTH) ? 'r' : '-');
    printf("%c", (st->st_mode & S_IWOTH) ? 'w' : '-');
    printf("%c", (st->st_mode & S_IXOTH) ? 'x' : '-');
    
    printf("\",\"type\":\"%s\",\"modified\":%ld,\"accessed\":%ld,\"changed\":%ld,"
           "\"inode\":%llu,\"device\":\"%ld\",\"hard_links\":%hu,\"block_size\":%d,\"blocks\":%lld}",
           file_type, st->st_mtime, st->st_atime, st->st_ctime,
           (unsigned long long)st->st_ino, (long)st->st_dev, st->st_nlink,
           st->st_blksize, (long long)st->st_blocks);
}

void handle_list_files(int id, const char* directory) {
    DIR *dir = opendir(directory);
    if (!dir) {
        send_error(id, "directory_error", "Cannot open directory");
        return;
    }
    
    printf("{\"jsonrpc\":\"2.0\",\"id\":%d,\"result\":[", id);
    
    struct dirent *entry;
    struct stat st;
    int first = 1;
    
    while ((entry = readdir(dir))) {
        if (entry->d_name[0] == '.') continue;
        
        char fullpath[2048];
        snprintf(fullpath, sizeof(fullpath), "%s/%s", directory, entry->d_name);
        
        if (stat(fullpath, &st) == 0) {
            print_file_json_compact(directory, entry->d_name, &st, first);
            first = 0;
        }
    }
    
    printf("]}\n");
    fflush(stdout);
    closedir(dir);
}

char* extract_string_value(const char* json, const char* key) {
    char search_pattern[256];
    snprintf(search_pattern, sizeof(search_pattern), "\"%s\":\"", key);
    
    char *start = strstr(json, search_pattern);
    if (!start) return NULL;
    
    start += strlen(search_pattern);
    char *end = strchr(start, '"');
    if (!end) return NULL;
    
    int len = end - start;
    char *result = malloc(len + 1);
    strncpy(result, start, len);
    result[len] = '\0';
    
    return result;
}

int extract_id(const char* json) {
    char *id_start = strstr(json, "\"id\":");
    if (!id_start) return -1;
    
    id_start += 5;
    return atoi(id_start);
}

int main() {
    send_initialization();
    
    char buffer[4096];
    while (fgets(buffer, sizeof(buffer), stdin)) {
        buffer[strcspn(buffer, "\n")] = 0;
        
        int id = extract_id(buffer);
        
        if (strstr(buffer, "\"method\":\"tools/list\"")) {
            send_tools_list(id);
        }
        else if (strstr(buffer, "\"name\":\"list_files\"")) {
            char *directory = extract_string_value(buffer, "directory");
            if (directory) {
                handle_list_files(id, directory);
                free(directory);
            } else {
                send_error(id, "invalid_params", "Missing directory parameter");
            }
        }
        else if (strstr(buffer, "\"method\":\"initialize\"")) {
            printf("{\"jsonrpc\":\"2.0\",\"id\":%d,\"result\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{\"tools\":{\"listChanged\":true}},\"serverInfo\":{\"name\":\"FileSavantAI\",\"version\":\"1.0.0\"}}}\n", id);
            fflush(stdout);
        }
    }
    
    return 0;
}