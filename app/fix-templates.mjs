import pg from 'pg';

const client = new pg.Client({
    host: 'localhost',
    port: 5432,
    database: 'mindsethappybot',
    user: 'postgres',
    password: 'postgres'
});

async function fixTemplates() {
    try {
        await client.connect();
        console.log('Connected to database');

        // Get current columns
        const cols = await client.query(`
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'question_templates'
        `);
        const existingCols = cols.rows.map(r => r.column_name);
        console.log('Existing columns:', existingCols);

        // Add missing columns
        const columnsToAdd = [
            { name: 'is_active', type: 'BOOLEAN DEFAULT true NOT NULL' },
            { name: 'updated_at', type: 'TIMESTAMP DEFAULT now() NOT NULL' }
        ];

        for (const col of columnsToAdd) {
            if (!existingCols.includes(col.name)) {
                console.log(`Adding ${col.name} column...`);
                await client.query(`ALTER TABLE question_templates ADD COLUMN ${col.name} ${col.type}`);
                console.log(`${col.name} added!`);
            }
        }

        console.log('Done!');
    } catch (err) {
        console.error('Error:', err.message);
    } finally {
        await client.end();
    }
}

fixTemplates();
