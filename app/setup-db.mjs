import pg from 'pg';

const client = new pg.Client({
    host: 'localhost',
    port: 5432,
    database: 'postgres',
    user: 'postgres',
    password: 'postgres'
});

async function createDb() {
    try {
        await client.connect();
        console.log('Connected to postgres');

        // Check if database exists
        const res = await client.query("SELECT 1 FROM pg_database WHERE datname = 'mindsethappybot'");
        if (res.rows.length === 0) {
            console.log('Creating database mindsethappybot...');
            await client.query('CREATE DATABASE mindsethappybot');
            console.log('Database created!');
        } else {
            console.log('Database already exists');
        }
    } catch (err) {
        console.error('Error:', err.message);
    } finally {
        await client.end();
    }
}

createDb();
