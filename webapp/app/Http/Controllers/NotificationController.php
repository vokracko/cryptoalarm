<?php

namespace Cryptoalarm\Http\Controllers;

use Illuminate\Http\Request;
use Cryptoalarm\Watchlist;
use Cryptoalarm\Notification;

class NotificationController extends Controller
{
    public function createMany(Request $request)
    {
        $data = json_decode($request->getContent(), true);
        
        foreach($data['transactions'] as $t) {
            // error_log(var_export($t, True));
            $item = Notification::create([
                'watchlist_id' => $data['watchlist_id'],
                'block_id' => $t[1],
                'tx_hash' => $t[2],
            ]);
        }

        return response()->json([], 200);
    }
}
