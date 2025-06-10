#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <dirent.h>
#include <time.h>

void print_file_info(struct stat *st, const char *name) {
    // Print permissions, links, owner, group, size, date, time, filename
    char *user = getpwuid(st->st_uid)->pw_name;
    char *group = getgrgid(st->st_gid)->gr_name;
    char datebuf[16];
    char timebuf[16];
    strftime(datebuf, sizeof(datebuf), "%b %d", localtime(&st->st_mtime));
    strftime(timebuf, sizeof(timebuf), "%H:%M", localtime(&st->st_mtime));
    printf("%o %ld %s %s %ld %s %s %s\n",
        st->st_mode & 0777, st->st_nlink, user, group,
        st->st_size, datebuf, timebuf, name);
}

int main() {
    DIR *dir = opendir(".");
    if (!dir) { perror("opendir"); return 1; }

    struct dirent *entry;
    while ((entry = readdir(dir))) {
        if (entry->d_name[0] == '.') continue; // Skip hidden files
        struct stat st;
        if (stat(entry->d_name, &st) == -1) { perror("stat"); continue; }
        print_file_info(&st, entry->d_name);
    }
    closedir(dir);
    return 0;
}