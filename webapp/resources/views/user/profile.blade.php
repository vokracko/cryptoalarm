@extends('layouts.app')

@section('content')
<div class="container">
    @include('messages.all')
    <h1>Edit profile</h1>

    {{ Form::open(['UserController@edit', $item->id]) }}
        <div class="form-group">
            {{ Form::label('email_template', 'Email template') }}
            {{ Form::textarea('email_template', $item->email_template, ['class' => 'form-control', 'placeholder' => $email_template ]) }}
        </div>
        <div class="form-group">
            You can use placeholders to positions information in your emails:
            <ul>
                <li><code>{name}</code> - watchlist name</li>
                <li><code>{coin}</code> - coin name</li>
                <li><code>{address}</code> - address hash</li>
                <li><code>{txs}</code> - list of transactions</li>
            </ul>
            Both address and transaction will contain link to blockchain explorer by default.
        </div>

        <div class="form-group">
            {{ Form::submit('Save profile', ['class' => 'form-control btn btn-primary']) }}
        </div>
    {{ Form::close() }}
<div>
@endsection