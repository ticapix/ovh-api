#/bin/sh

set -e
set -x

for f in schema/apis-*.json; do
    echo $f
    # check that there is only one body param with no name per params array
    cat $f | jq '.apis[].operations[].parameters    # extract all parameters
    | [.[] | [.paramType, .name]]                   # create array of tuple (paramType, name)
    | select(.[] | .[1] == null)                    # select params with an unmaned body param
    | [ .[][0] ]                                    # select all types
    | [.[] | select(. == "body")]                   # select only body type param
    | length | select( . != 1)                      # calculate number of body param
    ' | wc -l | grep '^0$'

    cat $f | jq '.apis[].operations[].parameters    # extract all parameters
    | [.[] | [.paramType, .dataType]]               # create array of tuple (paramType, name)
 '

    # cat $f | jq '.apis[].operations[].parameters'
done
