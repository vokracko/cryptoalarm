<?php

use Illuminate\Database\Seeder;

class UsersTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $rows = [
            'alice',
            'bob',
            'carol',
            'dave',
        ];

        foreach($rows as $row) {
            DB::table('users')->insert([
                'name' => $row,
                'email' => $row . "@cryptoalarm.tld",
                'password' => bcrypt($row),
                'email_template' => null,
            ]);
        }
    }
}
