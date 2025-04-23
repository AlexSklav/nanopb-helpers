#ifndef ___PB_EEPROM__H___
#define ___PB_EEPROM__H___

#include <avr/eeprom.h>
#include <pb_cpp_api.h>
#include "nanopb.h"


namespace nanopb {

inline UInt8Array eeprom_to_array(uint16_t eeprom_addr, UInt8Array output) {
  uint16_t payload_size = 0;

  // Read 2 bytes from EEPROM at the start address to get the payload size
  eeprom_read_block(
    reinterpret_cast<void*>(&payload_size),
    reinterpret_cast<const void*>(static_cast<uintptr_t>(eeprom_addr)),
    sizeof(payload_size)
  );

  // Check if the provided buffer is large enough
  if (output.length < payload_size) {
    // Not enough space — clear output to signal failure
    output.data = NULL;
    output.length = 0;
  } else {
    // Read payload from EEPROM (right after the 2-byte size field)
    eeprom_read_block(
      reinterpret_cast<void*>(output.data),
      reinterpret_cast<const void*>(static_cast<uintptr_t>(eeprom_addr + sizeof(uint16_t))),
      payload_size
    );
    output.length = payload_size;
  }

  return output;
}


inline void array_to_eeprom(uint16_t eeprom_addr, UInt8Array data) {
  // Disable interrupts during EEPROM write to prevent corruption
  cli();

  // Write the payload size (2 bytes) at the start address
  eeprom_update_block(
    reinterpret_cast<void*>(&data.length),
    reinterpret_cast<void*>(static_cast<uintptr_t>(eeprom_addr)),
    sizeof(uint16_t)
  );

  // Write the actual payload data right after the size
  eeprom_update_block(
    reinterpret_cast<void*>(data.data),
    reinterpret_cast<void*>(static_cast<uintptr_t>(eeprom_addr + sizeof(uint16_t))),
    data.length
  );

  // Re-enable interrupts
  sei();
}


template <typename Obj, typename Fields>
bool decode_obj_from_eeprom(uint16_t eeprom_addr, Obj &obj,
                          Fields const &fields, UInt8Array pb_buffer) {
  // Try to read the serialized message from EEPROM
  pb_buffer = eeprom_to_array(eeprom_addr, pb_buffer);

  // Check if reading from EEPROM was successful
  if (pb_buffer.data == NULL) {
    return false;
  }

  // Attempt to decode the buffer into the object
  return decode_from_array(pb_buffer, fields, obj);
}


template <typename Msg, typename Validator>
class EepromMessage : public Message<Msg, Validator> {
public:
  typedef Message<Msg, Validator> base_type;
  using base_type::_;
  using base_type::fields_;
  using base_type::buffer_;
  using base_type::reset;
  using base_type::serialize;
  using base_type::validate;

  EepromMessage(const pb_msgdesc_t *fields) : base_type(fields) {}

  EepromMessage(const pb_msgdesc_t *fields, size_t buffer_size, uint8_t *buffer)
    : base_type(fields, buffer_size, buffer) {}

  EepromMessage(const pb_msgdesc_t *fields, UInt8Array buffer)
    : base_type(fields, buffer) {}

  void load(uint8_t eeprom_addr=0) {
    // Try to load message from EEPROM at the specified address
    if (!decode_obj_from_eeprom(eeprom_addr, _, fields_, buffer_)) {
      // Message could not be loaded from EEPROM; reset to defaults
      reset();
    }
    // Always validate the message after loading (or resetting)
    validate();
  }

  void save(uint8_t eeprom_addr=0) {
    // Serialize the message to the buffer
    UInt8Array serialized = serialize();

    // If serialization was successful, save to EEPROM
    if (serialized.data != NULL) {
      array_to_eeprom(eeprom_addr, serialized);
    }
  }
};


} // namespace nanopb

#endif  // #ifndef ___PB_EEPROM__H___
