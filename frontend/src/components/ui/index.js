/**
 * UI Components Index
 * Centralized exports for all reusable UI components
 */

import ButtonComponent from './Button';
import InputComponent from './Input';
import CardComponent from './Card';
import ModalComponent from './Modal';
import DropdownComponent from './Dropdown';

export { ButtonComponent as Button };
export { InputComponent as Input };
export { CardComponent as Card };
export { ModalComponent as Modal };
export { DropdownComponent as Dropdown };

// Re-export component variants for convenience
export {
  ButtonComponent as Btn,
  InputComponent as TextField,
  CardComponent as Panel,
  ModalComponent as Dialog,
  DropdownComponent as Select
};
