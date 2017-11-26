<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Notification extends Model
{
    public $fillable = ['watchlist_id', 'tx_hash'];

    public function watchlist() 
    {
        return $this->belongsTo('App\Watchlist', 'watchlist_id');
    }
}
