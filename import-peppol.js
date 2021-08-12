const fs = require('fs');
const readline = require('readline');
const readInterface = readline.createInterface({
    input: fs.createReadStream('/Users/michiel/Downloads/directory-export-business-cards.csv'),
    output: fs.createWriteStream('/Users/michiel/gh/pondersource/peppol-python-demo/peppol-import.sql'),
    console: false
});

function balancedQuotes(str) {
  let count = 0;
  let fromPos = 0;
  let pos;
  while (true) {
    pos = str.indexOf('"', fromPos);
    if (pos === -1) {
        // console.log(count);
        return count % 2 === 0;          
    }
    // console.log({ str, fromPos, pos, count });
    fromPos = pos + 1;
    if (pos === 0 || str[pos-1] !== '\\') {
      count++;
    }
  }
}

// const str1 = '"iso6523-actorid-upis::9907:psctsm61t55l797p";"FARM. PASCUCCI D.SSA TERESA MARIA";"IT";"VIA MAZZINI, 1 - 47035 GAMBETTOLA (FC)";"IT:CF";"02389380409";"";"Office Contact Point\n' +
// 'Technical Contact Point\n' +
// 'Process Contact Point";"Nessun Riferimento\n' +
// 'NON_PRESENTE\n' +
// 'NON_PRESENTE";"';
// const str2 = '"iso6523-actorid-upis::0195:sguen201431858r";"KCJ AIr-\\" con Specialist Pte.Ltd. (en)";"SG";"10 Raeburn Park #04-03B Singapore";"";"";"";"";"";"";"";;"2020-12-30";"busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#conformant#urn:fdc:peppol.eu:2017:poacc:billing:international:sg:3.0::2.1\n' +
// 'busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2::CreditNote##urn:cen.eu:en16931:2017#conformant#urn:fdc:peppol.eu:2017:poacc:billing:international:sg:3.0::2.1"\n';

// console.log(balancedQuotes(str1));
// console.log(balancedQuotes(str2));
// process.exit(0);




function scanTerm (rest) {
    if (rest.length === 0) {
        return false;
    }
    if (rest[0] === '"') {
        let fromPos = 1;
        let pos;
        do {
          pos = rest.indexOf('"', fromPos);
        //   console.log({ rest, fromPos, pos });
          fromPos = pos + 1;
        } while (rest[pos-1] == '\\');
        // console.log('returning', {
        //     term: rest.substring(1, pos),
        //     rest: rest.substring(pos + 2)
        // });
        return {
            term: rest.substring(1, pos ),
            rest: rest.substring(pos + 2)
        };

    } else if (rest[0] === ';') {
        return {
            term: undefined,
            rest: rest.substring(1)
        }
    } else {
        throw new Error('parse error ' + rest);
    }
}

function scanEntry (entry) {
    let rest = entry;
    let arr = [];
    while (true) {
        const result = scanTerm(rest);
        if (!result) {
          return arr;
        }
        arr.push(result.term);
        rest = result.rest;
    }
}

// console.log(scanEntry('"Fredericia Kommune - B�rnehuset \\"\\"Valhalla\\"\\"";"DK";;"OrgNr";"69116418";"";"";"";"";"";;"2020-05-15";"busdox-docid-qns::urn:oasis:names:specification:' +
//     'ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1\n' +
//     'busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2::CreditNote##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1"'));

let headers;
let entry = '';
readInterface.on('line', function(line) {
  entry += line;
  // console.log('ENTRY:', entry);
  if (!entry.endsWith('"') || !balancedQuotes(entry)) {
    entry += '\n';
    return;
  }
//   console.log({ entry });
  arr = scanEntry(entry);
  if (!headers) {
  headers = arr;
  console.log('HEADERS:', headers);
  } else {
    // console.log(arr);
  }
  entry = '';
});