<?php

use Illuminate\Database\Seeder;

class WatchlistsTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $rows = [
            [1, 1, 'inout', 'rest', 'w1'],
            [2, 2, 'in', 'email', 'w2'],
            [3, 3, 'out', 'email', 'w3'],
            [4, 4, 'inout', 'email', 'w4'],
            [5, 1, 'out', 'rest', 'w5'],
            [6, 1, 'in', 'rest', 'w6'],
        ];

        foreach($rows as $row) {
            DB::table('watchlists')->insert([
                'name' => $row[4],
                'type' => $row[2],
                'notify' => $row[3],
                'address_id' => $row[0],
                'user_id' => $row[1],
            ]);
        }
    }
}
