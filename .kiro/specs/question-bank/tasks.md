# Implementation Plan

- [x] 1. Create admin question creation endpoint





  - Create POST /admin/questions/create endpoint in backend/main.py or new backend/question_bank_routes.py
  - Implement admin authorization check using auth.get_current_user and is_admin flag
  - Add Pydantic schema AdminQuestionCreate in backend/schemas.py for request validation
  - Implement validation for category (Quants, Logical, Language), difficulty (Easy, Medium, Hard), and correct_answer (A-D)
  - Create Question model instance and save to database
  - Create AdminActionLog entry with action_type="create_question" and question details
  - Invalidate category cache after successful creation
  - Return AdminQuestionResponse with question id and success message
  - _Requirements: 6.3, 6.4, 6.5_

- [x] 2. Add Pydantic schemas for admin question creation





  - Add AdminQuestionCreate schema in backend/schemas.py with all required fields
  - Add field validation: title (5-500 chars), description (10-5000 chars), category regex, difficulty regex, correct_answer regex
  - Add AdminQuestionResponse schema with id, title, category, topic, difficulty, created_at, message
  - Add optional sub_topic field with max 100 characters
  - Set default xp_reward to 10 with range validation (5-100)
  - _Requirements: 6.3, 6.6_

- [x] 3. Create AdminQuestionForm component





  - Create frontend/src/components/AdminQuestionForm.js component
  - Implement form with fields: title, description, category dropdown, topic input, sub_topic input, difficulty radio buttons
  - Add four option textareas (option_a, option_b, option_c, option_d)
  - Add correct_answer radio buttons (A, B, C, D)
  - Add explanation textarea and xp_reward number input
  - Implement client-side validation for all required fields
  - Add form state management using useState hook
  - Style form with TailwindCSS matching existing design
  - _Requirements: 6.3, 6.6_

- [x] 4. Implement form submission and error handling





  - Add handleSubmit function in AdminQuestionForm component
  - Make POST request to /admin/questions/create endpoint with form data
  - Implement loading state during submission with disabled submit button
  - Display server-side validation errors next to respective form fields
  - Show success message on successful creation
  - Clear form after successful submission
  - Add error handling for network errors and unauthorized access
  - _Requirements: 6.4, 6.5, 6.6_

- [x] 5. Add admin question creation button to QuestionBank component





  - Modify frontend/src/components/QuestionBank.js to check if user is admin
  - Add "Add Question" button in header, visible only to admin users
  - Implement modal or navigation to AdminQuestionForm when button is clicked
  - Pass current category and topic as default values to form if available
  - _Requirements: 6.1, 6.2_

- [x] 6. Implement modal for AdminQuestionForm





  - Create modal wrapper component or use existing modal pattern
  - Add open/close state management in QuestionBank component
  - Display AdminQuestionForm inside modal overlay
  - Add close button and backdrop click to close modal
  - Prevent body scroll when modal is open
  - Style modal with TailwindCSS for responsive design
  - _Requirements: 6.1, 6.2_

- [ ] 7. Add cache invalidation after question creation
  - Clear sessionStorage category cache in AdminQuestionForm after successful submission
  - Trigger category data refetch in QuestionBank component
  - Clear question cache in QuestionBank component
  - Update question count in UI without full page reload
  - _Requirements: 6.7_

- [ ] 8. Add topic autocomplete suggestions
  - Fetch existing topics from categories data in AdminQuestionForm
  - Implement autocomplete dropdown for topic input field
  - Filter topics based on selected category
  - Allow custom topic entry if not in suggestions
  - Style autocomplete dropdown with TailwindCSS
  - _Requirements: 6.3_

- [ ] 9. Add "Question Bank" button to Navigation component
  - Modify frontend/src/components/Navigation.js to add "Question Bank" button in header
  - Add navigation link to /question-bank route
  - Highlight button when on question-bank route using useLocation hook
  - Style button consistently with existing navigation items
  - _Requirements: 1.1, 1.2_

- [ ] 10. Write backend tests for admin question creation
  - Create test file backend/tests/test_question_bank.py
  - Write test for successful question creation with valid admin user
  - Write test for unauthorized access with non-admin user
  - Write test for validation errors (invalid category, difficulty, correct_answer)
  - Write test for duplicate title prevention
  - Write test for admin action log creation
  - Write test for cache invalidation
  - _Requirements: 6.3, 6.4, 6.5, 6.6_

- [ ] 11. Write frontend tests for AdminQuestionForm
  - Create test file frontend/src/components/__tests__/AdminQuestionForm.test.js
  - Write test for form rendering with all fields
  - Write test for client-side validation messages
  - Write test for successful form submission
  - Write test for error handling and display
  - Write test for form reset after submission
  - Mock API calls using jest and testing-library
  - _Requirements: 6.3, 6.4, 6.5, 6.6_

- [ ] 12. Add loading states and skeleton loaders
  - Ensure QuestionBank component shows skeleton loaders while fetching questions
  - Add loading spinner in AdminQuestionForm during submission
  - Disable form inputs during submission to prevent duplicate submissions
  - Add loading state for category data fetch
  - Style loading states consistently with existing patterns
  - _Requirements: 8.4_

- [ ] 13. Implement breadcrumb navigation enhancements
  - Verify breadcrumb navigation works correctly in QuestionBank component
  - Ensure breadcrumbs show: Categories > [Category] > [Topic]
  - Make breadcrumb items clickable to navigate back
  - Style breadcrumbs with TailwindCSS
  - Test navigation flow from questions back to categories
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 14. Add visual feedback and hover effects
  - Ensure category cards have hover effects in QuestionBank component
  - Add hover effects to topic cards
  - Add hover effects to question cards
  - Ensure difficulty badges have distinct colors (green for Easy, yellow for Medium, red for Hard)
  - Add transition animations for smooth hover effects
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 15. Implement empty state messages
  - Add "No questions available" message when topic has no questions
  - Add appropriate icon or illustration for empty state
  - Style empty state message with TailwindCSS
  - Ensure message is friendly and helpful
  - _Requirements: 8.5_

- [ ] 16. Test complete user flow end-to-end
  - Test navigation from dashboard to question bank
  - Test category selection and topic browsing
  - Test question filtering by difficulty
  - Test question sorting by date, difficulty, and title
  - Test question detail view navigation
  - Test back navigation at each level
  - Verify URL parameters update correctly
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 17. Test admin question creation flow end-to-end
  - Test admin user can see "Add Question" button
  - Test non-admin user cannot see "Add Question" button
  - Test opening question creation form/modal
  - Test filling out all form fields with valid data
  - Test form validation for each field
  - Test successful question submission
  - Test question appears in appropriate category/topic immediately
  - Test admin action log entry is created
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [ ] 18. Verify mobile responsiveness
  - Test QuestionBank component on mobile viewport
  - Test AdminQuestionForm modal on mobile viewport
  - Ensure category cards stack properly on mobile
  - Ensure form fields are usable on mobile
  - Test navigation and back buttons on mobile
  - Verify touch interactions work correctly
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 19. Add error boundary for graceful error handling
  - Create ErrorBoundary component if not exists
  - Wrap QuestionBank and AdminQuestionForm with ErrorBoundary
  - Display user-friendly error message when component crashes
  - Log errors to console for debugging
  - Add retry button in error boundary UI
  - _Requirements: 8.4_

- [ ] 20. Update documentation
  - Update README.md with Question Bank feature description
  - Document admin question creation process
  - Add API endpoint documentation for /admin/questions/create
  - Document required admin privileges
  - Add screenshots or GIFs of feature in action (optional)
  - _Requirements: 6.1, 6.2, 6.3_
