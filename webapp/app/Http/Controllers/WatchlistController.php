<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Notification;
use App\Watchlist;
use App\Coin;
use App\Setting;

class WatchlistController extends Controller
{
    public function rules()
    {
        return [
            'name'=>'required',
            'address'=> 'required',
            'type'=> 'required',
            'coin'=> 'required',
            'notify' => 'required',
            'email_template' => 'nullable',
        ];
    }

    public function show($id)
    {
        $item = Watchlist::where('user_id', auth()->user()->id)->findOrFail($id);
        $list = Notification::where('watchlist_id', $item->id)->paginate(50);
        $skipped = ($list->currentPage() * $list->perPage()) - $list->perPage();
        
        return view('watchlist.show', compact('list', 'item', 'skipped'));
    }

    public function index()
    {
        $list = Watchlist::where('user_id', auth()->user()->id)->paginate(50);
        $skipped = ($list->currentPage() * $list->perPage()) - $list->perPage();
        
        return view('watchlist.index',compact('list', 'skipped'));
    }

    public function create()
    {
        $email_template = Setting::findOrFail('email_template')->value;
        $coins = Coin::getPairs();
        
        return view('watchlist.create', compact('coins', 'email_template'));
    }

    public function store(Request $request)
    {
        $item = new Watchlist();
        $data = $this->validate($request, $this->rules());
        $item->saveItem($data);

        return redirect('/watchlist')->with('success', 'Item created!');
    }

    public function edit($id)
    {
        $email_template = Setting::findOrFail('email_template')->value;
        $item = Watchlist::where('user_id', auth()->user()->id)->findOrFail($id);
        $coins = Coin::getPairs();

        return view('watchlist.edit', compact('item', 'id', 'coins', 'email_template'));
    }

    public function update(Request $request, $id)
    {
        $item = new Watchlist();
        $data = $this->validate($request, $this->rules());
        $data['id'] = $id;
        error_log($data['type']);
        $item->updateItem($data);

        return redirect('/watchlist')->with('success', 'Item has been updated!');
    }

    public function destroy($id)
    {
        $item = Watchlist::findOrFail($id);
        $item->delete();

        return redirect('/watchlist')->with('success', 'Item has been deleted!');
    }
}
