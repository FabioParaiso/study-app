#!/bin/bash
BASE_URL="http://localhost:8000"

# 1. Login
echo "Logging in..."
USER_NAME="CurlUser$(date +%s)"
LOGIN_RES=$(curl -s -X POST "$BASE_URL/students" -H "Content-Type: application/json" -d "{\"name\": \"$USER_NAME\"}")
STUDENT_ID=$(echo $LOGIN_RES | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "Student ID: $STUDENT_ID"

if [ -z "$STUDENT_ID" ]; then
    echo "Login failed. Response: $LOGIN_RES"
    exit 1
fi

# 2. Upload File A
echo "Uploading File A (Math)..."
echo "Matematica" > math.txt
curl -s -X POST "$BASE_URL/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "student_id=$STUDENT_ID" \
  -F "file=@math.txt" > /dev/null

# 3. Upload File B (History)
echo "Uploading File B (History)..."
echo "Historia" > history.txt
curl -s -X POST "$BASE_URL/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "student_id=$STUDENT_ID" \
  -F "file=@history.txt" > /dev/null

# 4. List Materials
echo "Listing Materials..."
LIST_RES=$(curl -s "$BASE_URL/materials?student_id=$STUDENT_ID")
echo $LIST_RES

# Check if both files are listed
if [[ $LIST_RES == *"math.txt"* ]] && [[ $LIST_RES == *"history.txt"* ]]; then
    echo "SUCCESS: Both files found in library."
else
    echo "FAILURE: Files not found in list."
    exit 1
fi

# 5. Activate File A
# We need ID of File A.
# This simple script checks output, extracting ID is hard with grep, but we can assume ID 1 and 2 if fresh DB or just check status code.
# Let's get ID from list output using python or dumb grep.
ID_A=$(echo $LIST_RES | grep -o '"id":[0-9]*,"source":"math.txt"' | cut -d':' -f2 | cut -d',' -f1)
echo "Activating Material ID: $ID_A"

ACTIVATE_RES=$(curl -s -X POST "$BASE_URL/materials/$ID_A/activate?student_id=$STUDENT_ID")
echo "Activate Response: $ACTIVATE_RES"

if [[ $ACTIVATE_RES == *"activated"* ]]; then
    echo "SUCCESS: Activation successful."
else
    echo "FAILURE: Activation failed."
    exit 1
fi

# 6. Verify Active Material
CURRENT_RES=$(curl -s "$BASE_URL/current-material?student_id=$STUDENT_ID")
if [[ $CURRENT_RES == *"math.txt"* ]]; then
    echo "SUCCESS: Current material is math.txt"
else
    echo "FAILURE: Current material mismatch. Got: $CURRENT_RES"
    exit 1
fi

echo "ALL BACKEND TESTS PASSED"
rm math.txt history.txt
