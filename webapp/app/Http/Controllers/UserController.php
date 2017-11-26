<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Setting;

class UserController extends Controller
{
    public function edit()
    {
        $item = auth()->user();
        $email_template = Setting::findOrFail('email_template')->value;

        return view('user.profile', compact('item', 'email_template'));
    }

    public function update(Request $request)
    {
        $user = auth()->user();
        $data = $this->validate($request, [
            'email_template' => 'nullable',
        ]);
        $user->email_template = $data['email_template'];
        $user->save();

        return redirect('/profile')->with('success', 'Item has been updated!');
    }
}
