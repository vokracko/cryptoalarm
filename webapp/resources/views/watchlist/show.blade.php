@extends('layouts.app')

@section('content')
<div class="container">
    @include('messages.all')
    <h1>Watchlist detail: {{ $item->name }} </h1>

    <a href="{{ action('WatchlistController@edit', $item->id) }}" class="btn btn-primary">Edit</a><br>
    {{ Form::open(['method' => 'DELETE', 'action' => ['WatchlistController@destroy', $item->id]]) }}
        <button class="btn btn-danger" type="submit">Delete</button>
    {{ Form::close() }}
    
    <br>
    Coin: {{ $item->address->coin->name }}<br>
    Address: <a href="{{ $item->address->coin->explorer_url . $item->address->hash }}">{{ $item->address->hash }}</a><br>
    Type: {{ Cryptoalarm\Watchlist::getKeyedEnum('types', $item->type) }}<br>
    Notify: {{ Cryptoalarm\Watchlist::getKeyedEnum('notifyTypes', $item->notify) }}<br>
    Email template: <br>
    <pre>
        {{ $item->email_template }}
    </pre><br>

    <h2>Notifications</h2>
    @include('notification.list')
</div>
@endsection
