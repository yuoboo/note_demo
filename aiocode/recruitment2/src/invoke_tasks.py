from invoke import task

# from web_server import start_server


@task
def lint(c):
    c.run('pylint .')


# @task
# def server(c):
#     start_server()


@task
def worker(c):
    c.run('celery -A celery_worker:celery_app worker -l info -c 1')
