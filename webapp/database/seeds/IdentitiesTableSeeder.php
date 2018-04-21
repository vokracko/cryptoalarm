<?php

use Illuminate\Database\Seeder;
class IdentitiesTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $db = \Config::get('database.connections.pgsql.database');
        $host = \Config::get('database.connections.pgsql.hostname');
        $user = \Config::get('database.connections.pgsql.username');
        $pass = \Config::get('database.connections.pgsql.password');

        exec(sprintf('psql postgresql://%s:%s@%s/%s -c "\COPY identities (url, label, source, address_id) FROM \'identities.csv\' delimiter \';\' csv;"', $user, $pass, $host, $db));
        DB::query("select setval('identities_id_seq', (SELECT MAX(id) FROM identities) + 1);");
    }
}
