FROM postgres:15

ARG DB_USER
USER ${DB_USER}
ENV POSTGRES_PASSWORD=postgres
ARG DB_PASSWORD
ARG DB_REPL_PASSWORD
ARG DB_REPL_USER

COPY init.sql docker-entrypoint-initdb.d/

RUN echo "CREATE USER $DB_REPL_USER WITH REPLICATION LOGIN PASSWORD '$DB_REPL_PASSWORD';" >> docker-entrypoint-initdb.d/init.sql
RUN echo "ALTER ROLE $DB_USER PASSWORD '$DB_PASSWORD';" >> docker-entrypoint-initdb.d/init.sql 

CMD ["postgres"]
