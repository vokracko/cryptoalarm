<h1>{{ $title }}</h1>
<div class="form-group">
    {{ Form::label('name', 'Name:') }}
    {{ Form::text('name', isset($item) ? $item->name : '', ['class' => "form-control"]) }}
</div>
<div class="form-group">
    {{ Form::label('type', 'Type:') }}
    {{ Form::select('type', App\Watchlist::getEnum('type'), isset($item) ? $item->type : '', ['class' => "form-control"]) }}
</div>
<div class="form-group">
    {{ Form::label('coin', 'Coin:') }}
    {{ Form::select('coin', $coins, isset($item) ? $item->address->coin->id : '', ['class' => "form-control"]) }}
</div>
<div class="form-group">
    {{ Form::label('address', 'Address:') }}
    {{ Form::text('address', isset($item) ? $item->address->hash : '', ['class' => "form-control"]) }}
</div>
<div class="form-group">
    {{ Form::label('notify', 'Notification:') }}
    {{ Form::select('notify', App\Watchlist::getEnum('notifyType'), isset($item) ? $item->notify : '', ['class' => "form-control"]) }}
</div>
{{ Form::submit($title, ['class' => "form-control btn btn-primary"]) }}