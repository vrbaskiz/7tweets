from fabric.api import local, run, env, settings

env.user = 'root'
env.hosts = ['break.sedamcvrkuta.com']

network_name = 'radionica'
image_tag = 'delicb/radionica'
db_container_name = 'radionica-postgres'
db_user = 'radionica'
db_name = 'radionica'
db_port = 5432
db_image = 'postgres:9.6.2'
db_volume = 'radionica-postgres-data'

gunicorn_port = 8000
external_port = 80

service_container_name = 'seventweets'


def create_network():
    with settings(warn_only=True):
        run(f'docker network create {network_name}')


def create_volume():
    with settings(warn_only=True):
        run(f'docker volume create {db_volume}')


def start_db(db_pass):
    with settings(warn_only=True):
        run(f'docker run -d --name {db_container_name} --net {network_name} '
            f'-v {db_volume}:/var/lib/postgresql/data '
            f'--restart unless-stopped -e POSTGRES_USER={db_user} '
            f'-e POSTGRES_PASSWORD={db_pass} '
            f'-e POSTGRES_DB={db_name} '
            f'-p 127.0.0.1:{db_port}:{db_port} {db_image}')


def pull_image(tag=image_tag):
    run(f'docker pull {tag}')


def migrate(db_pass, image=image_tag):
    run(f'docker run '
        f'--rm '
        f'--net {network_name} '
        f'-e ST_DB_USER={db_user} -e ST_DB_PASS={db_pass} '
        f'-e ST_DB_HOST={db_container_name} '
        f'-e ST_DB_NAME={db_name} '
        f'{image} '
        f'python3 -m seventweets migrate')


def start_service(db_pass, image=image_tag):
    run(f'docker run -d '
        f'--name {service_container_name} '
        f'--net {network_name} '
        f'-e ST_DB_USER={db_user} '
        f'-e ST_DB_PASS={db_pass} '
        f'-e ST_DB_HOST={db_container_name} '
        f'-e ST_DB_NAME={db_name} '
        f'-e ST_DB_PORT={db_port} '
        f'-p 0.0.0.0:{external_port}:{gunicorn_port} '
        f'{image}')


def stop_service():
    with settings(warn_only=True):
        run(f'docker stop {service_container_name}')
        run(f'docker rm {service_container_name}')


def build_image(tag=image_tag):
    local(f'docker build -t {tag} . --build-arg PORT={gunicorn_port}')


def push_image(tag=image_tag):
    local(f'docker push {tag}')


def app_logs():
    run(f'docker logs {service_container_name}')


def deploy(db_pass, image=image_tag):
    build_image(image)
    push_image(image)
    pull_image(image)
    create_network()
    stop_service()
    create_volume()
    start_db(db_pass)
    migrate(db_pass)
    start_service(db_pass, image)
