#include <stdio.h>
#include <sys/stat.h>
#include <dirent.h>
#include <pwd.h>
#include <grp.h>
#include <time.h>
#include <string.h>
#include <unistd.h>

void print_file_info_json(const char *directory, const char *filename, struct stat *st) {
    // Get owner and group names
    struct passwd *pwd = getpwuid(st->st_uid);
    struct group *grp = getgrgid(st->st_gid);
    
    // Determine file type
    const char *file_type;
    if (S_ISDIR(st->st_mode)) file_type = "directory";
    else if (S_ISREG(st->st_mode)) file_type = "file";
    else if (S_ISLNK(st->st_mode)) file_type = "symlink";
    else if (S_ISCHR(st->st_mode)) file_type = "char_device";
    else if (S_ISBLK(st->st_mode)) file_type = "block_device";
    else if (S_ISFIFO(st->st_mode)) file_type = "fifo";
    else if (S_ISSOCK(st->st_mode)) file_type = "socket";
    else file_type = "unknown";
    
    // Build full path
    char fullpath[2048];
    if (strcmp(directory, ".") == 0) {
        snprintf(fullpath, sizeof(fullpath), "%s", filename);
    } else {
        snprintf(fullpath, sizeof(fullpath), "%s/%s", directory, filename);
    }
    
    // Print JSON object
    printf("{\n");
    printf("  \"name\": \"%s\",\n", filename);
    printf("  \"path\": \"%s\",\n", fullpath);
    printf("  \"size\": %lld,\n", (long long)st->st_size);
    printf("  \"owner\": \"%s\",\n", pwd ? pwd->pw_name : "unknown");
    printf("  \"group\": \"%s\",\n", grp ? grp->gr_name : "unknown");
    printf("  \"uid\": %d,\n", st->st_uid);
    printf("  \"gid\": %d,\n", st->st_gid);
    printf("  \"permissions\": \"%03o\",\n", st->st_mode & 0777);
    printf("  \"permissions_readable\": \"");
    
    // Print human-readable permissions
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
    printf("\",\n");
    
    printf("  \"type\": \"%s\",\n", file_type);
    printf("  \"modified\": %ld,\n", st->st_mtime);
    printf("  \"accessed\": %ld,\n", st->st_atime);
    printf("  \"changed\": %ld,\n", st->st_ctime);
    printf("  \"inode\": %llu,\n", (unsigned long long)st->st_ino);
    printf("  \"device\": \"%ld\",\n", (long)st->st_dev);
    printf("  \"hard_links\": %hu,\n", st->st_nlink);
    printf("  \"block_size\": %d,\n", st->st_blksize);
    printf("  \"blocks\": %lld\n", (long long)st->st_blocks);
    printf("}");
}

int main(int argc, char *argv[]) {
    const char *path = (argc > 1) ? argv[1] : ".";
    DIR *dir = opendir(path);
    if (!dir) {
        printf("{\n");
        printf("  \"error\": \"Cannot open directory\",\n");
        printf("  \"directory\": \"%s\"\n", path);
        printf("}\n");
        return 1;
    }
    
    struct dirent *entry;
    struct stat st;
    int first_file = 1;
    
    printf("[\n");
    
    while ((entry = readdir(dir))) {
        if (entry->d_name[0] == '.') continue; // skip hidden files
        
        char fullpath[2048];
        snprintf(fullpath, sizeof(fullpath), "%s/%s", path, entry->d_name);

        if (stat(fullpath, &st) == 0) {
            if (!first_file) {
                printf(",\n");
            }
            print_file_info_json(path, entry->d_name, &st);
            first_file = 0;
        }
    }
    
    printf("\n]\n");
    closedir(dir);
    return 0;
}