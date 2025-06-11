#include <stdio.h>
#include <sys/stat.h>
#include <dirent.h>

int main(int argc, char *argv[]) {
    const char *path = (argc > 1) ? argv[1] : ".";
    DIR *dir = opendir(path);
    if (!dir) return 1;
    
    struct dirent *entry;
    struct stat st;
    
    while ((entry = readdir(dir))) {
        if (entry->d_name[0] == '.') continue;
        
        char fullpath[2048];
        snprintf(fullpath, sizeof(fullpath), "%s/%s", path, entry->d_name);

        if (stat(fullpath, &st) == 0) {
            printf("%lld bytes  %s\n", (long long)st.st_size, entry->d_name);
        }
    }
    
    closedir(dir);
    return 0;
}