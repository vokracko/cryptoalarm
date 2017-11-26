<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Address extends Model
{
    protected $table = 'addresses';
    protected $fillable = ['coin_id', 'hash'];
    public $timestamps = false;

    public function coin()
    {
        return $this->belongsTo('App\Coin', 'coin_id');
    }
}
