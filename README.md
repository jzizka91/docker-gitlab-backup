# Gitlab Backup

### Daily-Backup
Script will clone all repositories, if they don't exists yet. If repositories already exists, only changes will be pulled.

#### Daily-Backup Usage
```
docker run \
    --name $name \
    --volume /root/.ssh:/root/.ssh:rw \
    --volume /mnt/storage/backup/gitlab-daily:/backup:rw \
    --env TOKEN=<TOKEN_KEY> \
    <docker-gitlab-backup-image>
```
#### Change GROUPID
```
--env GROUPID=<gitlab-group-id> \
```
