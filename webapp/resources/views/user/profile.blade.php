@extends('layouts.app')

@section('content')
<div class="container">
    @include('messages.all')
    <h1>Edit profile</h1>

    {{ Form::open(['UserController@edit', $item->id]) }}


        <div class="form-group">
            {{ Form::submit('Save profile', ['class' => 'form-control btn btn-primary']) }}
        </div>
    {{ Form::close() }}
<div>
@endsection