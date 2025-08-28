#!/bin/bash
set -e

# Function to get collections array - Add or modify collections here
get_collections() {
    echo "['users', 'linkedin_tokens', 'linkedin_posts']"
}

echo "Starting MongoDB initialization..."

# Start MongoDB without authentication
mongod --bind_ip_all --noauth &
pid=$!

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to start..."
until mongosh --quiet --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
  echo "Waiting for MongoDB to be ready..."
  sleep 2
done

echo "MongoDB started, setting up users and databases..."

# Create the root user
mongosh admin --eval "
  if (!db.getUser('$MONGO_INITDB_ROOT_USERNAME')) {
    db.createUser({
      user: '$MONGO_INITDB_ROOT_USERNAME',
      pwd: '$MONGO_INITDB_ROOT_PASSWORD',
      roles: [ 'root' ]
    });
    print('Root user created');
  } else {
    print('Root user already exists');
  }
"

# Create application database and user
mongosh "$MONGO_INITDB_DATABASE" --eval "
  if (!db.getUser('$MONGO_INITDB_ROOT_USERNAME')) {
    db.createUser({
      user: '$MONGO_INITDB_ROOT_USERNAME',
      pwd: '$MONGO_INITDB_ROOT_PASSWORD',
      roles: [{ role: 'dbOwner', db: '$MONGO_INITDB_DATABASE' }]
    });
    print('Database user created');
  } else {
    print('Database user already exists');
  }

  const collections = $(get_collections);
  collections.forEach(collection => {
    try {
      if (!db.getCollection(collection).exists()) {
        db.createCollection(collection);
        print('Created collection:', collection);
      } else {
        print('Collection already exists:', collection);
      }
    } catch(err) {
      print('Error with collection', collection + ':', err);
    }
  });
"

echo "MongoDB initialization completed"

# Gracefully stop the background MongoDB process
kill $pid
wait $pid

echo "Starting MongoDB with authentication enabled..."
exec mongod --bind_ip_all --auth
