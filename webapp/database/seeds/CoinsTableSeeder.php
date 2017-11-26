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
            ['BTC', 495417, 'https://blockchain.info/search?search='],
            ['BCH', 0, 'sdfds'],
            ['LTC', 1317496, 'http://explorer.litecoin.net/search?q='],
            ['DASH', 774952, 'https://explorer.dash.org/search?q='],
            ['ZEC', 224115, 'https://explorer.zcha.in/search?q='],
            ['ETH', 4595349, 'https://etherscan.io/search?q='],
        ];

        foreach($rows as $row) {
            DB::table('coins')->insert([
                'name' => $row[0],
                'last_block' => $row[1],
                'explorer_url' => $row[2],
            ]);
        }
    }
}
