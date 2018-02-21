<?php

namespace Cryptoalarm;

use Illuminate\Database\Eloquent\Model;

class Address extends Model
{
    protected $table = 'addresses';
    protected $fillable = ['coin_id', 'hash'];
    public $timestamps = false;

    public function coin()
    {
        return $this->belongsTo('Cryptoalarm\Coin', 'coin_id');
    }
}
