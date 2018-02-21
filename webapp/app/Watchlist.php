<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Traits\Enums;
use App\Address;

class Watchlist extends Model
{
    use Enums;

    protected $fillable = ['name', 'address_id', 'user_id', 'type', 'email_template'];
    public $timestamps = false;
    public $type_text = null;

    protected $enumTypes = [
        'in' => 'Input',
        'out' => 'Output',
        'inout' => 'Input & output',
    ];

    public function address()
    {
        return $this->belongsTo('App\Address', 'address_id');
    }

    public function saveItem($data)
    {
        $this->user_id = auth()->user()->id;
        $this->name = $data['name'];
        $this->address_id = $this->matchAddress($data['coin'], $data['address']);
        $this->type = $data['type'];
        $this->email_template = $data['email_template'];
        $this->save();
    }

    public function updateItem($data)
    {
        $item = $this->findOrFail($data['id']);
        $item->user_id = auth()->user()->id;
        $item->name = $data['name'];
        $item->address_id = $this->matchAddress($data['coin'], $data['address']);
        $item->type = $data['type'];
        $item->email_template = $data['email_template'];
        $item->save();
    }

    public function matchAddress($coin, $hash)
    {
        return Address::firstOrCreate([
            'coin_id' => Coin::findOrFail($coin)->id,
            'hash' => $hash,
        ])->id;
    }
}
