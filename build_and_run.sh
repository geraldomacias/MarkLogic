docker-compose -f docker-compose-dev.yml build
docker-compose -f docker-compose-dev.yml up -d
docker-compose -f docker-compose-dev.yml run users python manage.py recreate_db
docker-compose -f docker-compose-dev.yml run file_system python manage.py recreate_db
docker-compose -f docker-compose-dev.yml run machine_learning python manage.py recreate_db
