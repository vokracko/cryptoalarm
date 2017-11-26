<?php

use Illuminate\Database\Seeder;

class AddressesTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $rows = [
            ['1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp', 1],
            ['1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY', 2],
            ['LhyLNfBkoKshT7R8Pce6vkB9T2cP2o84hx', 3],
            ['XpESxaUmonkq8RaLLp46Brx2K39ggQe226', 4],
            ['t1KLGj3izuKveu1eFZUiwp3BEKHQAiYv2Z7', 5],
            ['0xfbb1b73c4f0bda4f67dca266ce6ef42f520fbb98', 6],
        ];

        foreach($rows as $row) {
            DB::table('addresses')->insert([
                'hash' => $row[0],
                'coin_id' => $row[1],
            ]);
        }
    }
}
