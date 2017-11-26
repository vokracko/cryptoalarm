<?php

use Illuminate\Database\Seeder;

class NotificationsTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $rows = [
            [1, '8fbef41f6d7d575a9ae03216f9f981ba29c50ef8b223c3856e6fc0a6093a1160'],
            [2, 'd2986e12d509c3de9405833c7502423da59f846a91763a7fc7e004029e1ef433'],
            [3, 'cdb482b37f2545acb1333dd1c63410b0a71c79ec524f6b89d8564baded57a2ed'],
            [4, '93ad57a283f6fc626eafc612b8a6ac20334207f3bfe77687e70d96b303cfe964'],
            [5, '1ba6d664127cc36b4e9d68ebe5e18b9c6b250d90e0551f8b4065c04c46c5a9e8'],
            [6, '0x5575ba0e02af2bbc186a956df8ee51bdd448eeb537b76ad23fd52989fb970662']
        ];

        foreach($rows as $row) {
            DB::table('notifications')->insert([
                'watchlist_id' => $row[0],
                'tx_hash' => $row[1],
                'created_at' => date("Y-m-d H:i:s"),
            ]);
        }
    }
}
