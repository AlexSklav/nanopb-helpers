#ifndef ___PB_UPDATE_MESSAGE__H___
#define ___PB_UPDATE_MESSAGE__H___

#include <pb_common.h>

#ifdef LOGGING
#define LOG(...) printf(__VA_ARGS__)
#else
#define LOG(...)
#endif


struct MessageUpdateBase {
  /* Define behaviour to update an existing nano-protocol buffer message
   * `struct`, based on the contents of a (possibly partial) secondary message.
   * */

  struct IterPair {
    pb_field_iter_t source;  /* Reference to field in source struct. */
    pb_field_iter_t target;  /* Reference to field in target struct. */
  };

  struct Parent {
    const pb_msgdesc_t *descriptor;  /* Start of the pb_msgdesc_t */
    pb_size_t tag;                   /* Tag of the field */
  };

  Parent parents[5];
  pb_size_t parent_count;

  MessageUpdateBase() { reset(); }

  void reset() { parent_count = 0; }

  template <typename Fields, typename Message>
  void update(Fields fields, Message &source, Message &target) {
    reset();
    LOG("\n**************************************************\n");
    __update__(fields, (void *)&source, (void *)&target);
  }

  virtual bool process_field(IterPair &iter, pb_size_t count) = 0;
private:

  template <typename Iter>
  pb_size_t extract_count(Iter &iter) {
    pb_type_t type = iter.type;
    pb_size_t count = 0;

    /* Load the count of the data for the current field in the source
      * structure. */
    if (PB_HTYPE(type) == PB_HTYPE_OPTIONAL && *(bool*)(iter.pSize)) {
      count = 1;
    } else if (PB_HTYPE(type) == PB_HTYPE_REPEATED) {
      count = *(pb_size_t*)(iter.pSize);
    } else if (PB_HTYPE(type) == PB_HTYPE_REQUIRED) {
      count = 1;
    }
    return count;
  }

  template <typename Fields>
  void __update__(Fields fields, void *source, void *target) {
    /* Iterate through each field in the Protocol Buffer message defined by
     * `fields`.
     *
     * For each field, call `process_field` method to assess whether or not the
     * corresponding data from the source structure should be copied to the
     * target structure. */
    IterPair iter;

    if (!pb_field_iter_begin(&iter.source, fields, source)) {
      return; /* Empty message type */
    }

    if (!pb_field_iter_begin(&iter.target, fields, target)) {
      return; /* Empty message type */
    }

    do {
      pb_type_t type;
      pb_size_t count = 0;
      type = iter.source.type;

      /* TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO */
      /* TODO Define behaviour for non-static types, e.g., repeated. */
      /* TODO  - Repeated:
       *        * Copy up to count.
       *        * Do not process sub-message.
       *        * Set new count. */
      /* TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO */

      if (PB_ATYPE(type) == PB_ATYPE_STATIC) {
        count = extract_count(iter.source);

        /* If the `process_field` method returns `true`... */
        if (process_field(iter, count)) {
          /*  - Copy data from source structure to target structure. */
          memcpy(iter.target.pData, iter.source.pData,
                 iter.source.data_size);
          /*  - Update the `has_` field or the `_count` field of the target
           *    structure. */
          if (PB_HTYPE(type) == PB_HTYPE_OPTIONAL) {
            *(bool*)iter.target.pSize = *(bool*)iter.source.pSize;
          } else if (PB_HTYPE(type) == PB_HTYPE_REPEATED) {
            *(pb_size_t*)iter.target.pSize = *(pb_size_t*)iter.source.pSize;
          }
        }
        LOG(">> source_count=%d, LTYPE=%d\n",
               count, PB_LTYPE(iter.source.type));

        /* If the current field is a sub-message, push parent message onto
         * parent stack and process sub-message fields. */
        if ((count > 0) && (PB_LTYPE(iter.source.type) ==
                            PB_LTYPE_SUBMESSAGE)) {
          /*  - Mark sub-message types as present if they are present in the
           *    source message. */
          *(bool*)iter.target.pSize = *(bool*)iter.source.pSize;

          parents[parent_count].descriptor = iter.source.descriptor;
          parents[parent_count].tag = iter.source.tag;
          parent_count++;
          for (pb_size_t i = 0; i < count; i++) {
            /* For repeated types, the count may be greater than one.  In such
             * cases, we need to iterate through each repeated sub-message to
             * handle each one separately.
             *
             * Note that we cast `pData` from a `void` pointer to a `uint8_t`
             * to avoid [compiler warnings][1] about pointer arithmetic
             * involving a `void` pointer.
             *
             * [1]: http://stackoverflow.com/questions/26755638/warning-pointer-of-type-void-used-in-arithmetic#26756220 */
            pb_size_t offset = i * iter.source.data_size;
            __update__(iter.source.submsg_desc,
                       ((uint8_t *)iter.source.pData) + offset,
                       ((uint8_t *)iter.target.pData) + offset);
          }
          --parent_count;
        }
        count = extract_count(iter.source);
        LOG("<< source_count=%d\n", count);
      } else {
        LOG("Unrecognized PB_ATYPE=%d\n", PB_ATYPE(type));
      }
    } while (pb_field_iter_next(&iter.source) && pb_field_iter_next(&iter.target));
  }
};


struct MessageUpdate : public MessageUpdateBase {
  using MessageUpdateBase::IterPair;

  MessageUpdate() : MessageUpdateBase() {}

  virtual bool process_field(IterPair &iter, pb_size_t count) {
    for (pb_size_t i = 0; i < parent_count; i++) LOG("  ");
    LOG("=========================================\n");
    for (pb_size_t i = 0; i < parent_count; i++) LOG("  ");
    if (parent_count > 0) {
      for (pb_size_t i = 0; i < parent_count; i++) {
        LOG("> %d ", parents[i].tag);
      }
      LOG("\n");
    }
    for (pb_size_t i = 0; i < parent_count; i++) LOG("  ");
    LOG("tag=%d descriptor=%p count=%d ltype=%x atype=%x htype=%x data_size=%d \n",
           iter.source.tag, iter.source.descriptor, count,
           PB_LTYPE(iter.source.type), PB_ATYPE(iter.source.type),
           PB_HTYPE(iter.source.type), iter.source.data_size);
    for (pb_size_t i = 0; i < parent_count; i++) LOG("  ");
    LOG("-----------------------------------------");

    bool trigger_copy = false;
    if (PB_LTYPE(iter.source.type) != PB_LTYPE_SUBMESSAGE) {
      /* Only copy all data for field if this is not a sub-message type, since
       * we want to handle sub-message fields one-by-one. */
      trigger_copy = (count > 0);
    }
    LOG("%c\n", (trigger_copy) ? 'W' : ' ');
    return trigger_copy;
  }
};


#endif  // #ifndef ___PB_UPDATE_MESSAGE__H___
