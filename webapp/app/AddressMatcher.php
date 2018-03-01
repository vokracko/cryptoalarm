<?php

namespace Cryptoalarm;

class AddressMatcher {
    public $coins = [
        'btc' => [ // https://en.bitcoin.it/wiki/Address
            '[1|3][[:alnum:]]{25,34}', // P2PKH/P@PS
            'bc1[[:alnum:]]{23,32}', // Bech32
        ],
        'eth' => ['0x[[:alnum:]]{40}'],
        'ltc' => ['[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}'], // https://stackoverflow.com/questions/23570080/how-to-determine-if-litecoin-address-is-valid
        'xmr' => ['4[0-9AB][[:alnum:]]{93}'], // https://getmonero.org/resources/moneropedia/address.html
        'zec' => ['[t|z]{34}'],
    ];

    public function identify_address($address) {
        global $coins;
        $result = [];

        foreach($this->coins as $coin => $regexes) {
            foreach($regexes as $regex) {
                if(preg_match('/^' . $regex . '$/', $address)) {
                    $result[] = $coin;
                    break;
                }
            }
        }

        return $result;
    }

    public function match_addresses($text) {
        global $coins;
        $results = [];

        foreach($this->coins as $coin => $regexes) {
            foreach($regexes as $regex) {
                $matches = [];
                # spaces so it doesnt match only parts of text
                $res = preg_match_all('/ ' . $regex . ' /', $text, $matches);

                if($res) {
                    foreach($matches[0] as $match) {
                        $results[trim($match)] = $coin;
                    }
                }
            }
        }
        
        return $results;
    }

}

