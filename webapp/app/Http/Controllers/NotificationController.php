<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Watchlist;
use App\Notification;

class NotificationController extends Controller
{
    public function createMany(Request $request)
    {
        $data = json_decode($request->getContent(), true);
        error_log($data['watchlist_id']);
        $watchlist = Watchlist::findOrFail($data['watchlist_id']);

        foreach($data['transactions'] as $t) {
            $item = Notification::create([
                'watchlist_id' => $watchlist->id,
                'tx_hash' => $t,
            ]);

            $item->save();
        }

        return response()->json([], 200);
    }
}
