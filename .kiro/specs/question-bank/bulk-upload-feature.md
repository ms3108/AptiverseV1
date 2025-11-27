# Bulk Upload Feature Documentation

## Overview

Added a bulk upload feature to the AdminQuestionForm component, allowing administrators to upload multiple questions at once via JSON file upload.

## Implementation Details

### Component Changes: `frontend/src/components/AdminQuestionForm.js`

#### New State Variables
```javascript
const [mode, setMode] = useState('single'); // 'single' or 'bulk'
const [selectedFile, setSelectedFile] = useState(null);
const [uploadProgress, setUploadProgress] = useState(null);
const [mergeStrategy, setMergeStrategy] = useState('merge');
```

#### New Features

1. **Tab Interface**
   - Two modes: "Single Question" and "Bulk Upload"
   - Users can switch between modes without losing data
   - Clean UI with active tab highlighting

2. **File Upload**
   - Accepts only `.json` files
   - Shows selected file name and size
   - Validates file type on selection

3. **Merge Strategies**
   - **Merge (Recommended)**: Updates existing questions by title, adds new ones
   - **Append**: Adds all questions as new (may create duplicates)
   - **Replace All**: Deletes all existing questions and adds new ones (with warning)

4. **Upload Process**
   - Shows upload progress indicator
   - Displays detailed success message with statistics (added, updated, deleted)
   - Comprehensive error handling with user-friendly messages
   - Auto-closes modal after successful upload

5. **User Guidance**
   - Instructions panel explaining JSON format requirements
   - Reference to `QUESTION_UPLOAD_FORMAT.md` documentation
   - Clear descriptions for each merge strategy

### API Integration

**Endpoint**: `POST /admin/questions/upload`

**Request**:
- Content-Type: `multipart/form-data`
- Authorization: Bearer token
- Form Data:
  - `file`: JSON file
  - `merge_strategy`: "merge" | "append" | "replace"

**Response**:
```json
{
  "message": "Questions uploaded successfully",
  "strategy": "merge",
  "stats": {
    "total_in_file": 10,
    "added": 5,
    "updated": 3,
    "deleted": 0
  }
}
```

### Error Handling

The implementation handles various error scenarios:

1. **File Validation**
   - Non-JSON files rejected
   - Empty file selection prevented

2. **Authentication Errors**
   - Session expiration detection
   - Permission denied handling

3. **Server Errors**
   - Invalid JSON format
   - Missing required fields
   - Network connectivity issues
   - Server-side processing errors

4. **User Feedback**
   - Clear error messages for each scenario
   - Success statistics display
   - Upload progress indication

### UI/UX Features

1. **Responsive Design**
   - Works on all screen sizes
   - Mobile-friendly file input
   - Proper spacing and layout

2. **Accessibility**
   - Proper labels for form inputs
   - Disabled states during upload
   - Clear visual feedback

3. **Visual Indicators**
   - Loading spinner during upload
   - Success/error message styling
   - File size display
   - Strategy descriptions with icons

### Code Structure

```javascript
// File selection handler
const handleFileSelect = (e) => {
    // Validates file type
    // Updates selectedFile state
    // Clears previous messages
}

// Bulk upload handler
const handleBulkUpload = async () => {
    // Validates file selection
    // Creates FormData with file and strategy
    // Sends POST request to API
    // Handles response and errors
    // Updates UI with results
    // Auto-closes on success
}
```

## Usage Instructions

### For Administrators

1. **Open the Add Questions Modal**
   - Click "Add Question" button in Question Bank

2. **Switch to Bulk Upload Mode**
   - Click "Bulk Upload" tab

3. **Select Merge Strategy**
   - Choose appropriate strategy based on needs
   - Default is "Merge" (safest option)

4. **Select JSON File**
   - Click "Choose File" or drag file
   - Only `.json` files accepted

5. **Upload**
   - Click "Upload Questions" button
   - Wait for confirmation
   - Review statistics

### JSON File Format

See `QUESTION_UPLOAD_FORMAT.md` for complete format specification.

**Minimal Example**:
```json
[
  {
    "title": "Sample Question",
    "description": "Question text here",
    "difficulty": "Easy",
    "topic": "Math",
    "option_a": "Option 1",
    "option_b": "Option 2",
    "option_c": "Option 3",
    "option_d": "Option 4",
    "correct_answer": "A",
    "explanation": "Explanation here",
    "xp_reward": 10
  }
]
```

## Testing Checklist

- [x] Tab switching works correctly
- [x] File selection validates JSON files only
- [x] All merge strategies work as expected
- [x] Upload shows progress indicator
- [x] Success message displays statistics
- [x] Error messages are clear and helpful
- [x] Modal auto-closes after success
- [x] File input resets after upload
- [x] Category cache invalidation works
- [x] Question list refreshes after upload
- [x] Disabled states prevent double submission
- [x] Responsive design works on mobile

## Benefits

1. **Efficiency**: Upload hundreds of questions at once
2. **Flexibility**: Multiple merge strategies for different scenarios
3. **Safety**: Default merge strategy prevents data loss
4. **Transparency**: Clear statistics on what was changed
5. **User-Friendly**: Simple interface with clear instructions
6. **Robust**: Comprehensive error handling

## Future Enhancements (Optional)

- Drag-and-drop file upload
- JSON validation preview before upload
- Download template button
- Export existing questions to JSON
- Batch edit functionality
- Upload history/logs

## Related Files

- `frontend/src/components/AdminQuestionForm.js` - Main component
- `backend/admin_questions.py` - Backend API endpoints
- `QUESTION_UPLOAD_FORMAT.md` - Format documentation
- `backend/starter_questions.json` - Example file

## Status

✅ **COMPLETE** - Bulk upload feature fully implemented and integrated with existing modal.
