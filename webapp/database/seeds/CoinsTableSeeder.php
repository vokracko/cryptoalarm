<?php

use Illuminate\Database\Seeder;

class CoinsTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $rows = [
            [1, 'BTC', 495417, 'https://blockchain.info/search?search='],
            [2, 'BCH', 0, 'https://explorer.bitcoin.com/bch/search/'],
            [3, 'LTC', 1317496, 'http://explorer.litecoin.net/search?q='],
            [4, 'DASH', 774952, 'https://explorer.dash.org/search?q='],
            [5, 'ZEC', 224115, 'https://explorer.zcha.in/search?q='],
            [6, 'ETH', 4595349, 'https://etherscan.io/search?q='],
            [7, 'XMR', NULL, ''],
        ];

        foreach($rows as $row) {
            DB::table('coins')->insert([
                'id' => $row[0],
                'name' => $row[1],
                'last_block' => $row[2],
                'explorer_url' => $row[3],
            ]);
        }
        DB::query("select setval('coins_id_seq', (SELECT MAX(id) FROM coins) + 1);");
    }
}
