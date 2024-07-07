#!/bin/bash

# Запуск первой ноды Cassandra
echo "Запускаем первую ноду Cassandra..."
docker-compose up -d cassandra-node1

echo "Запускаем первую ноду Cassandra..."
docker-compose up -d cassandra-node2

echo "Ожидаем запуска Cassandra (ожидание 150 секунд)..."
sleep 150

echo "Настройка базы данных Cassandra..."
docker exec -it cassandra-node1 cqlsh -e "\
CREATE KEYSPACE tweeter WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};

USE tweeter;

CREATE TABLE users (
  user_id uuid PRIMARY KEY,
  username text,
  password_hash text,
  created_at timestamp
);

CREATE TABLE posts (
  id uuid PRIMARY KEY,
  username text,
  content text,
  likes int
);

INSERT INTO users (user_id, username, password_hash, created_at) VALUES (uuid(), 'admin', 'admin', dateof(now()));
INSERT INTO users (user_id, username, password_hash, created_at) VALUES (uuid(), 'test', 'test', dateof(now()));
"

echo "База данных Cassandra настроена и заполнена данными.(admin:admin,test:test)"
